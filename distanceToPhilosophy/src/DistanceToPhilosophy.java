import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

public class DistanceToPhilosophy {
  
  private TokenDictionary tokenDictionary = new TokenDictionary();
  
  private final String startNode, redirectsFile, edgesFile;
  
  private Set<Integer> nodes = new HashSet<Integer>();
  private Map<Integer,Integer> redirects = new HashMap<Integer,Integer>();
  private Map<Integer,List<Integer>> edges = new HashMap<Integer,List<Integer>>();
  
  public static void main(String args[]) throws IOException {
  	if (args.length != 3) {
  		throw new RuntimeException("DistanceToPhilosophy <startNode> <redirectsFile> <edgesFile>");
  	}	
    new DistanceToPhilosophy(args).go();
  }
  
  public DistanceToPhilosophy(String[] args) {
    this.startNode = args[0];
    this.redirectsFile = args[1];
    this.edgesFile = args[2];
  }
  
  public void go() throws IOException {
    parseRedirectsFile();
    parseEdgesFile();
    breadthFirstWalk();    
  }

  private void parseRedirectsFile() throws IOException {    
    BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(redirectsFile)));
    System.err.println(new Date()+">parseRedirectsFile");
    int numIgnoredSlashN = 0, numNotIgnoredSlashN = 0;
    int numDuplicateRedirects = 0, numContradictoryRedirects = 0;
    int total = 0;

    String next;
    while((next=reader.readLine())!=null) {
      String[] cols = next.split("\t");
      if (cols[2].equals("\\N")) {
        numIgnoredSlashN++;
      }
      else {
        int fromNode = tokenDictionary.idxForToken(cols[1]);
        int toNode = tokenDictionary.idxForToken(cols[2]);
        if (redirects.containsKey(fromNode)) {
          if (redirects.get(fromNode) == toNode) {
            numDuplicateRedirects++;
          }
          else {
            numContradictoryRedirects++;
          }
        }
        redirects.put(fromNode, toNode);
        numNotIgnoredSlashN++;
      }
            
      if (++total%10000==0) {
        System.err.println(new Date()+" parsing.. total="+total+
            " numIgn\\N="+numIgnoredSlashN+
            " numNotIgn\\N="+numNotIgnoredSlashN+
            " numDupRed="+numDuplicateRedirects+
            " numConrRed="+numContradictoryRedirects+
            " idxToToken.size="+tokenDictionary.idxToToken.size());

      }
    }
    reader.close();

    //System.out.println("redirects "+redirects.toString());
    //System.out.println("tokenDictionary.idxToToken "+tokenDictionary.idxToToken.toString());
    //System.out.println("tokenDictionary.tokenToIdx "+tokenDictionary.tokenToIdx.toString());
    System.err.println(new Date()+"<parseRedirectsFile total="+total+
        " numIgn\\N="+numIgnoredSlashN+
        " numNotIgn\\N="+numNotIgnoredSlashN+
        " numDupRed="+numDuplicateRedirects+
        " numConrRed="+numContradictoryRedirects+
        " idxToToken.size="+tokenDictionary.idxToToken.size());
    
  }
  
  private void parseEdgesFile() throws FileNotFoundException, IOException {
    System.err.println(new Date()+"parseEdgesFile: reading from "+edgesFile);
    BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(edgesFile)));
    int linesProcessed=0;
    List<Integer> rawEdges = new LinkedList<Integer>();    
    
    // first read from file and just convert to idx    
    String next;    
    while((next=reader.readLine())!=null) {     
      String[] cols = next.split("\t");      
      int fromNode = tokenDictionary.idxForToken(cols[0]);
      int toNode = tokenDictionary.idxForToken(cols[1]);      
      
      nodes.add(fromNode);      
      rawEdges.add(fromNode);
      rawEdges.add(toNode);
      
      if (++linesProcessed%100000==0) {
        System.err.println("parseEdgesFile:"+
            " linesProcessed="+linesProcessed+
            " rawEdges.size()="+rawEdges.size()+
            " idxToToken.size="+tokenDictionary.idxToToken.size());
      }
    }
    if (!tokenDictionary.tokenToIdx.containsKey(startNode)) {
      throw new RuntimeException("after parsing stdin never saw starting node ["+startNode+"]");
    }
    reader.close();
    
    //System.out.println("raw edges "+rawEdges.toString());
    //System.out.println("tokenDictionary.idxToToken "+tokenDictionary.idxToToken.toString());
    
    // make another pass over the data first processing redirects
    // and checking toNodes actually point to a fromNode, else
    // ignore them
    List<Integer> confirmedEdges = new LinkedList<Integer>();
    int numRedirects=0, numSuccessfulCamelCasings=0, numUnsuccessfulCamelCasings=0, numExceptionsCamelCasings=0;
    linesProcessed=0;
    
    while(rawEdges.size() > 0) {      
      int fromNode = rawEdges.remove(0);
      int toNode = rawEdges.remove(0);
      
      // we always trust the fromNode but we need to do 
      // additional checking on the 'toNode'
      
      // 1) might need redirecting, 
      // though need to sanity check the redirect
      if (redirects.containsKey(toNode)) {
        int redirect = redirects.get(toNode);
        if (nodes.contains(redirect)) {
          System.err.println("parseEdgesFile: redirecting "+tokenDictionary.prettyEdgeForIdxs(toNode,redirect));
          toNode = redirect;
          numRedirects++;
        }
        else {
          System.err.println("parseEdgesFile: invalid redirect!! "+tokenDictionary.prettyEdgeForIdxs(toNode,redirect));          
        }
      }

      // check toNode is valid
      if (nodes.contains(toNode)) {
        confirmedEdges.add(fromNode);
        confirmedEdges.add(toNode);
      }
      else {
        String original = null;
        try {
          // 2) might need camel casing 
          //   eg '1949 Coupe de France Final' -> 'soccer' instead of 'Soccer'      
          original = tokenDictionary.idxToToken.get(toNode);
          String firstLetterCapitalised = original.substring(0,1).toUpperCase();
          if (original.length() > 1) { 
            firstLetterCapitalised += original.substring(1,original.length()).toLowerCase();
          }
          if (tokenDictionary.tokenToIdx.containsKey(firstLetterCapitalised)) {
            // seemed to work!
            toNode = tokenDictionary.tokenToIdx.get(firstLetterCapitalised);
            confirmedEdges.add(fromNode);
            confirmedEdges.add(toNode);
            numSuccessfulCamelCasings++;
          }
          else {
            // oh well, worth a try, have to ignore it
            System.err.println("parseEdgesFile: ignoring edge "+tokenDictionary.prettyEdgeForIdxs(fromNode,toNode)+
                ", (neither original["+original+"] or firstLetterCapitalised["+firstLetterCapitalised+"])");
            numUnsuccessfulCamelCasings++;
          }
        }
        catch (Exception e) {
          System.err.println("exception?? "+e.getMessage()+" checking camel casing for original=["+original+"]");
          numExceptionsCamelCasings++;
        }
      }
      
      if (++linesProcessed%100000==0) {
        System.err.println("confirming edges:"+
            " linesProcessed="+linesProcessed+
            " numRedirects="+numRedirects+
            " numSuccCC="+numSuccessfulCamelCasings+
            " numUnsuccCC="+numUnsuccessfulCamelCasings+
            " numExcepCC="+numExceptionsCamelCasings+
            " idxToToken.size="+tokenDictionary.idxToToken.size());
      }
      
    }

    System.err.println("confirming edges: (final) "+
        " linesProcessed="+linesProcessed+
        " numRedirects="+numRedirects+
        " numSuccCC="+numSuccessfulCamelCasings+
        " numUnsuccCC="+numUnsuccessfulCamelCasings+
        " numExcepCC="+numExceptionsCamelCasings+
        " idxToToken.size="+tokenDictionary.idxToToken.size());
        
    // now process edges...
    System.err.println(new Date()+">parseEdgesFile; building edges");
    while(confirmedEdges.size() > 0) {      
      // note: we are now +reversing+ the edges
      int toNode = confirmedEdges.remove(0);
      int fromNode = confirmedEdges.remove(0);      
      
      // build edges structure
      if (edges.containsKey(fromNode)) {
        List<Integer> outboundEdges = edges.get(fromNode);
        if (outboundEdges.contains(toNode)) {
          System.err.println("already an edge from "+fromNode+
              " ("+tokenDictionary.idxToToken.get(fromNode)+") to "+toNode+" ("+tokenDictionary.idxToToken.get(toNode)+")");
        } 
        else {
          outboundEdges.add(toNode);
        }         
      }
      else {        
        List<Integer> newSetOfEdges = new ArrayList<Integer>();
        newSetOfEdges.add(toNode);
        edges.put(fromNode, newSetOfEdges);
      }      
    }
    
    //System.out.println("edges "+edges.toString());
    //System.out.println("tokenDictionary.idxToToken "+tokenDictionary.idxToToken.toString());
  }

  private void breadthFirstWalk() {
    Queue<Integer> boundary = new LinkedList<Integer>();
    Set<Integer> visitedNodes = new HashSet<Integer>();    
    Set<Integer> unvisitedNodes = new HashSet<Integer>(nodes);

    int start = tokenDictionary.tokenToIdx.get(startNode);
    boundary.add(start);
    visitedNodes.add(start);
    unvisitedNodes.remove(start);
    
    int distance = 0;    
    while(boundary.size() != 0) {
      Queue<Integer> frontier = new LinkedList<Integer>();
      for(int boundaryNode : boundary) {
        System.out.println("FINAL "+tokenDictionary.idxToToken.get(boundaryNode) + "\t" + distance);
        visitedNodes.add(boundaryNode);
        unvisitedNodes.remove(boundaryNode);
        
        if (edges.containsKey(boundaryNode)) {
          for (int outboundNode : edges.get(boundaryNode)) {
            if (unvisitedNodes.contains(outboundNode)) {
              frontier.add(outboundNode);
            }
          }
        }        
      }
      System.err.println("distance="+distance+" frontier size "+frontier.size()+
          " visitedNodes.size="+visitedNodes.size()+
          " unvisitedNodes.size="+unvisitedNodes.size());      
      distance++;
      boundary = frontier;      
    }
    
    for (int node : unvisitedNodes) {
      System.out.println("didnt visit "+tokenDictionary.idxToToken.get(node));
    }
    
  }
  
}

